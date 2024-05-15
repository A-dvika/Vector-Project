import argparse
import os

import streamlit as st
from PIL import Image

from schema import Myntra
from vector_search import run_vector_search

def main(args):
    # Set page configuration
    st.set_page_config(
        page_title="Vefas (Vector Fashion Search)",
        page_icon=":dress:",
        layout="wide"
    )

    # Define title and sidebar options
    st.title("👗 Vefas (Vector Fashion Search)")
    st.markdown("*Your go-to tool for discovering fashion items using vectors!*")
    st.sidebar.title("🎨 Vector Search")

    # Sidebar inputs
    table_name = st.sidebar.text_input("Enter Table Name", args.table_name)
    search_query = st.sidebar.text_input("Enter Search Query", args.search_query)
    limit = st.sidebar.slider("Limit Results", args.limit_min, args.limit_max, args.limit_default)
    output_folder = st.sidebar.text_input("Output Folder Path", args.output_folder)

    # Image Based Search
    uploaded_image = st.sidebar.file_uploader("Upload an Image")
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.sidebar.image(image, caption="Uploaded Image", use_column_width=True)
        search_query = image  # Set the search query as the uploaded image

    # Text Based Search
    if st.sidebar.button("Search"):
        run_vector_search("~/.lancedb", table_name, Myntra, search_query, limit, output_folder)

    # Initialize session state for image index if it doesn't exist
    if "current_image_index" not in st.session_state:
        st.session_state.current_image_index = 0

    # Display images in output folder
    if os.path.exists(output_folder):
        image_files = [
            f
            for f in os.listdir(output_folder)
            if f.endswith(".jpg") or f.endswith(".png")
        ]
        if image_files:
            num_images = len(image_files)
            st.session_state.current_image_index %= num_images
            image_file = image_files[st.session_state.current_image_index]
            image_path = os.path.join(output_folder, image_file)
            image = Image.open(image_path)
            st.image(image, caption="Result", use_column_width=True)

            # Navigation buttons for previous and next images
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬅️ Previous"):
                    st.session_state.current_image_index = (
                        st.session_state.current_image_index - 1
                    ) % num_images
            with col2:
                if st.button("Next ➡️"):
                    st.session_state.current_image_index = (
                        st.session_state.current_image_index + 1
                    ) % num_images
        else:
            st.write("No images found in the output folder.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vector Search")
    parser.add_argument("--table_name", type=str, default="myntra", help="Name of the table")
    parser.add_argument("--search_query", type=str, default="", help="Search query")
    parser.add_argument("--limit_min", type=int, default=1, help="Minimum limit for number of results")
    parser.add_argument("--limit_max", type=int, default=10, help="Maximum limit for number of results")
    parser.add_argument("--limit_default", type=int, default=3, help="Default limit for number of results")
    parser.add_argument("--output_folder", type=str, default="output", help="Output folder path")
    args = parser.parse_args()
    main(args)
