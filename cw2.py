import click
import pandas as pd
import graphviz
import pydot
import plotly.express as px
import matplotlib.pyplot as plt
import pycountry_convert as pc

d_tiny = pd.read_json('datasets/sample_tiny.json', lines=True)
d_small = pd.read_json('datasets/sample_small.json', lines=True)
# d_100k_lines = pd.read_json('datasets/sample_100k_lines.json', lines=True)
# d_400k_lines = pd.read_json('datasets/sample_400k_lines.json', lines=True)

def country_code_to_continent(country_code):
    if country_code == "EU":
        return "European Union"
    elif country_code == "AP":
        return "Asia/Pacific Region"
    else:
        try:
            return pc.convert_continent_code_to_continent_name(pc.country_alpha2_to_continent_code(country_code))
        except KeyError:
            return "Unknown country"


def get_views_by_country(data, doc_uuid):
    fig = plt.figure(figsize=(10, 6))
    plt.title('Views by Country')
    plt.xlabel("Countries")
    plt.ylabel("No. of views")
    plt.hist(data[data['subject_doc_id'] == doc_uuid]['visitor_country'])
    return fig


def get_views_by_continent(data, doc_uuid):
    fig = plt.figure(figsize=(10, 6))
    plt.title('Views by Continent')
    plt.xlabel("Continents")
    plt.ylabel("No. of views")
    plt.hist(data[data['subject_doc_id'] == doc_uuid]['visitor_continent'])
    return fig


def get_visitor_useragents(data):
    fig = plt.figure(figsize=(10, 6))
    data['visitor_useragent'].value_counts().plot(kind='bar')
    plt.xlabel("Visitor User Agents")
    plt.ylabel("Frequency")
    return fig


def get_visitor_browsers(data):
    fig = plt.figure(figsize=(10, 6))
    data['visitor_browser'] = data['visitor_useragent'].str.split('/').str[0]
    data['visitor_browser'].value_counts().plot(kind='bar')
    plt.xlabel("Visitor Browsers")
    plt.ylabel("Frequency")
    plt.tight_layout()
    return fig


def get_avid_readers(data):
    return data.groupby('visitor_uuid').sum(numeric_only=True)['event_readtime'].sort_values(ascending=False).head(10)


def plot_avid_readers(data):
    fig = plt.figure(figsize=(11, 7))
    plt.tight_layout()
    get_avid_readers(data).sort_values(ascending=True).plot(kind='barh')
    plt.xlabel("Time in minutes")
    plt.ylabel("Visitor UUID")
    plt.tight_layout()
    return fig


# Req 5a
def get_doc_visitors(data, doc_uuid):
    readers = data[data['env_type'] == "reader"]
    return readers[readers['subject_doc_id'] == doc_uuid]['visitor_uuid'].unique()


# Req 5b
def get_visitor_docs(data, visitor_uuid):
    readers = data[data['env_type'] == "reader"]
    return readers[readers['visitor_uuid'] == visitor_uuid]['subject_doc_id'].dropna().unique()


# Req 5c, 5d
def also_like(data, doc_uuid, visitor_uuid, ascending, req_5=True):
    visitor_uuids = get_doc_visitors(data, doc_uuid)
    y = []
    for reader in visitor_uuids:
        for doc in get_visitor_docs(data, reader):
            if doc != doc_uuid and doc not in get_visitor_docs(data, visitor_uuid).tolist():
                print()
                y.append([reader, doc])
    if not req_5:
        for reader in visitor_uuids:
            y.append([reader, doc_uuid])
        return pd.DataFrame(y)
    try:
        if ascending:
            return pd.DataFrame(y).groupby(1).count().nsmallest(10, [0]).reset_index().tail(-1)
        else:
            return pd.DataFrame(y).groupby(1).count().nlargest(10, [0]).reset_index().tail(-1)
    except KeyError:
        print("Exception thrown")
        return pd.DataFrame(y)


# Req 6
def also_like_graph(data, doc_uuid, visitor_uuid, ascending):
    top_docs = also_like(data, doc_uuid, visitor_uuid, ascending, req_5=False)
    top_docs[0] = top_docs[0].str[-4:]
    top_docs[1] = top_docs[1].str[-4:]
    print(top_docs)
    dot = graphviz.Digraph()
    dot.node(visitor_uuid[-4:], visitor_uuid[-4:], stle='filled', fillcolor='green')
    dot.node(doc_uuid[-4:], doc_uuid[-4:], stle='filled', fillcolor='green')
    dot.edge(visitor_uuid[-4:], doc_uuid[-4:])
    for index, row in top_docs.iterrows():
        dot.node(str(row[0]), str(row[0]))
        dot.node(str(row[1]), str(row[1]))
        dot.edge(str(row[0]), str(row[1]))

    print(dot.source)

    dot.render('output.dot').replace('\\', '/')

    (graph,) = pydot.graph_from_dot_file('output.dot')
    graph.write_png('output.png')
    return 'output.png'


@click.command()
@click.option('-u', type=str, help="user_uuid")
@click.option('-d', type=str, help="doc_uuid")
@click.option('-t', type=str, help="task_id")
@click.option('-f', type=str, help="file_name")
def run_task(u, d, t, f):

    # 2a, 2b, 3a, 3b, 4, 5d, 6, 7
    if t == "2a":
        get_views_by_country(globals()[f"d_{f}"], d)
        plt.show()
    elif t == "2b":
        get_views_by_continent(globals()[f"d_{f}"], d)
        plt.show()
    elif t == "3a":
        get_visitor_useragents(globals()[f"d_{f}"])
        plt.show()
    elif t == "3b":
        get_visitor_browsers(globals()[f"d_{f}"])
        plt.show()
    elif t == "4":
        get_avid_readers(globals()[f"d_{f}"])
    elif t == "5d":
        # print(also_like('100713205147-2ee05a98f1794324952eea5ca678c026', '19c97695f06da354', False))
        also_like(globals()[f"d_{f}"], d, u, False)
    elif t == "6":
        also_like_graph(globals()[f"d_{f}"], d, u, False)


if __name__ == '__main__':
    run_task()

