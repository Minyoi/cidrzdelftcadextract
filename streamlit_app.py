import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

import requests
import os
from dotenv import load_dotenv
import argparse

load_dotenv()

token = os.getenv("TOKEN")
box_ip = os.getenv("BOX_IP")
api_root = f"{box_ip}/api/v2"

HEADERS = {"Authorization": f"Token {token}"}

series_url = f"{api_root}/series"
result_url = f"{api_root}/results"

# Helper function for making http requests via Python requests package
def get_requests(url, payload=None): 
    response = requests.get(url, headers=HEADERS, params=payload)
    response.raise_for_status()

    return response.json()


def get_series_instance_uids(url, payload=None):
    """
    Returns all Series Instance UIDs associated with the patient_id
    The SeriesInstanceUID is required as a parameter to fetch data 
    from the results endpoint
    """

    result = get_requests(url, payload)["results"]

    return set(map(lambda x: x.get("SeriesInstanceUID"), result))

def get_data(id, scores=False, normalized=False, heatmap=False):
    """ 
    Returns all results associated with the Series Instance UIDs

    The results of interest include:
        'CAD4TB 7' - results associated with the scores
        'Original' - results associated with the normalized image
        'Texture Overlay' - results associated with the heatmap
    
    The results returned are dictionary objects; hence specific 
    values are contained in the 'value' field
    eg.  {
            ...
            ... 
            'value': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx.png'
            ...
         }
    """

    names = ('CAD4TB 7','Original','Texture Overlay')
    payload = {
        "SeriesInstanceUID": id
        }

    # Set results for scores only
    if scores == True:
        payload["name"] = names[0] 
    # Set results for normalized images only
    elif normalized:
        payload["name"] = names[1]
    # Set results for heatmaps only
    elif heatmap:
        payload["name"] = names[2]
    # Set results for all three (scores, normalized image and heatmap)
    else:
        payload["name"] = names
    
    return get_requests(result_url, payload)["results"]
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get Patient ID')
    parser.add_argument('--pid', type=str, required=True,
                        help='patient id to get details')

    parser.add_argument('--algotype', type=str, choices=['scores',
                        'normalized', 'heatmap'],
                        help='algorithm type to get related information')

    patient_id = parser.parse_args().pid
    algorithm_type = None
    if parser.parse_args().algotype:
        algorithm_type = parser.parse_args().algotype
    payload = {
            'PatientID': patient_id
        }
    
    # Get all patient related series instance uids 
    series_instance_uids = get_series_instance_uids(series_url, payload)

    # Get only score results related to series instance uids 
    if algorithm_type == "scores":
        print(list(map(lambda x: get_data(x, scores=True), series_instance_uids)))

    # Get only normalized image results related to series instance uids 
    elif algorithm_type == "normalized":
        print(list(map(lambda x: get_data(x, normalized=True), series_instance_uids)))

    # Get only heatmap results related to series instance uids 
    elif algorithm_type == "heatmap":
        print(list(map(lambda x: get_data(x, heatmap=True), series_instance_uids)))

    else:
        # Get all results related to series instance uids 
        print(list(map(get_data, series_instance_uids)))
    

   
    

    