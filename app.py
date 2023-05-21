import gradio as gr
from cw2 import *

data_tiny = pd.read_json('datasets/sample_tiny.json', lines=True)
data_small = pd.read_json('datasets/sample_small.json', lines=True)
data_100k_lines = pd.read_json('datasets/sample_100k_lines.json.gz', lines=True, compression='gzip')
data_400k_lines = pd.read_json('datasets/sample_400k_lines.json.gz', lines=True, compression='gzip')
data_600k_lines = pd.read_json('datasets/sample_600k_lines.json.gz', lines=True, compression='gzip')

for dataset in [data_tiny, data_small, data_100k_lines, data_400k_lines, data_600k_lines]:
    dataset['visitor_continent'] = dataset['visitor_country'].apply(country_code_to_continent)


def req_1(doc_uuid, data):
    return get_views_by_country(globals()[f"data_{data}"], doc_uuid), \
           get_views_by_continent(globals()[f"data_{data}"], doc_uuid)


def change(data):
    return get_visitor_useragents(globals()[f"data_{data}"]), get_visitor_browsers(globals()[f"data_{data}"])


def req_4(data):
    return get_avid_readers(globals()[f"data_{data}"]).reset_index().reset_index(), \
           plot_avid_readers(globals()[f"data_{data}"])


def req_5_and_6(doc, vis, sort, data):
    return also_like(globals()[f"data_{data}"], doc, vis, sort == "Ascending"), \
           also_like_graph(globals()[f"data_{data}"], doc, vis, sort == "Ascending")


with gr.Blocks(css="""
                    #graph {width: 50%; margin: auto;}
                    .mx-auto {width: 70%; margin: auto;}
                    #space_between {justify-content: space-between}
                    #submit_button {background-color: red;}
                """) as demo:
    gr.Markdown("""
        # Data Analysis of a Document Tracker
        This assignment requires us to develop a simple Python-based application, that analyses and displays document tracking data from a major web site. 
        
        The issuu.com platform is a web site for publishing documents. It is widely used by many on-line publishers and currently hosts about 15 million documents. The web site tracks usage of the site and makes the resulting, anonymised data available to a wider audience. For example, it records who views a certain document, the browser used for viewing it, the way how the user arrived at this page etc. In this exercise, we use one of these data sets to perform data processing and analysis in Python. 
        
        The data format uses JSON and is described on this local page, describing the data spec. Note that the data files contain a sequence of entries in JSON format, rather than one huge JSON construct, in order to aid scalability
    
        This project was built using python 3.10 and following are the implemented functionalities of all the required tasks. Tune the following inputs and click on respective buttons to get the desired output:
        
        ## Requirement 2: Views by country/continent
    """)
    with gr.Row():
        with gr.Column(scale=1, variant='panel', elem_id="space_between"):
            t2a_doc_uuid = gr.Textbox(value="140228101942-d4c9bd33cc299cc53d584ca1a4bf15d9", label="Enter document UUID:")
            selected_dataset = gr.Radio(label="Choose dataset size:",
                                        choices=['tiny', 'small', '100k_lines', '400k_lines', '600k_lines'],
                                        interactive=True,
                                        value='small')
            req_1_submit = gr.Button(value="Generate graphs", elem_id="submit_button")
    with gr.Column(scale=2):
        with gr.Row():
            views_by_country = gr.Plot(value=get_views_by_country(globals()[f"data_{selected_dataset.value}"], t2a_doc_uuid.value))
            views_by_continent = gr.Plot(value=get_views_by_continent(globals()[f"data_{selected_dataset.value}"], t2a_doc_uuid.value))

    req_1_submit.click(fn=req_1, inputs=[t2a_doc_uuid, selected_dataset], outputs=[views_by_country, views_by_continent])

    gr.Markdown("""
        ## Requirement 3: Views by browser
        
        We want to identify the most popular browser. To this end, the application has to examine the visitor useragent field and count the number of occurrences for each value in the input file.
    """)
    with gr.Column():
        with gr.Row():
            with gr.Column(scale=1, variant='panel', elem_id="space_between"):
                selected_dataset_3 = gr.Radio(label="Choose dataset size:",
                                              choices=['tiny', 'small', '100k_lines', '400k_lines', '600k_lines'],
                                              interactive=True,
                                              value='small')
        with gr.Row():
            all_browsers = gr.Plot(value=get_visitor_useragents(data_tiny))
            main_browsers = gr.Plot(value=get_visitor_browsers(data_tiny))

        selected_dataset_3.change(fn=change, inputs=selected_dataset_3, outputs=[all_browsers, main_browsers])

    gr.Markdown("""
        ## Requirement 4: Reader profiles
        
        We want to identify the most avid readers. We want to determine, for each user, the total time spent reading documents. The top 10 readers, based on this analysis, are printed below.:
        """)

    with gr.Column():
        with gr.Row():
            with gr.Column(scale=1, variant='panel', elem_id="space_between"):
                selected_dataset_4 = gr.Radio(label="Choose dataset size:",
                                              choices=['tiny', 'small', '100k_lines', '400k_lines', '600k_lines'],
                                              interactive=True,
                                              value='small')
        with gr.Row():
            with gr.Column(scale=2):
                avid_readers = gr.Dataframe(
                    headers=["#", "Visitor UUID", "Total Page Read Time"],
                    value=get_avid_readers(data_tiny).reset_index().reset_index(),
                    row_count=10,
                    col_count=3,
                )
            with gr.Column(scale=3):
                avid_readers_plot = gr.Plot(value=plot_avid_readers(data_tiny))

        selected_dataset_4.change(fn=req_4, inputs=selected_dataset_4, outputs=[avid_readers, avid_readers_plot])

    gr.Markdown("""
        ## Requirement 5 & 6: "Also likes" functionality and graph
        
        Popular document-hosting web sites, such as Amazon, provide information about related documents based on document tracking information. One such feature is the “also likes” functionality: for a given document, identify, which other documents have been read by this document’s readers.
        """)
    with gr.Row():
        with gr.Column(scale=1, variant='panel', elem_id="space_between"):
            selected_dataset_5 = gr.Radio(label="Choose dataset size:",
                                          choices=['tiny', 'small', '100k_lines', '400k_lines', '600k_lines'],
                                          interactive=True,
                                          value='small')
            t5_doc_uuid = gr.Textbox(value="100713205147-2ee05a98f1794324952eea5ca678c026", label="Enter document UUID:")
            t5_visitor_uuid = gr.Textbox(value="19c97695f06da354", label="Enter visitor UUID:")
            t5_sorting = gr.Radio(choices=['Ascending', 'Descending'], value='Ascending', label="Specify the sorting function:")
            req_5_submit = gr.Button(value="Submit", elem_id="submit_button")
        with gr.Column(scale=1):
            also_likes_df = gr.Dataframe(value=also_like(globals()[f"data_{selected_dataset_5.value}"], t5_doc_uuid.value, t5_visitor_uuid.value,
                                                         t5_sorting.value == 'Ascending'),
                                         headers=["Document UUID", "Count"])

    gr.Markdown("""
        For the above “also like” functionality, this section generates a graph that displays the relationship between the input document and all documents that have been found as “also like” documents (and only these documents)
        """)
    also_likes_graph = gr.Image(value=also_like_graph(globals()[f"data_{selected_dataset_5.value}"], t5_doc_uuid.value, t5_visitor_uuid.value,
                                                t5_sorting.value == 'Ascending'))

    req_5_submit.click(fn=req_5_and_6, inputs=[t5_doc_uuid, t5_visitor_uuid, t5_sorting, selected_dataset_5], outputs=[also_likes_df, also_likes_graph])

demo.launch()
