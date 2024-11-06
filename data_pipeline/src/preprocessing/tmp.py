from preprocess_dataset import (
    get_section_names, segment_by_sections, remove_irrelevant_information,
    replace_blanks, numbers_to_array, ordered_list_to_string, sex,
    discharge_condition, no_change, preprocess, flatten_dict, chunk_json_string
)
import torch
from data_pipeline.dags.create_embedding import (get_embedding, embed_to_str, embed)

data = {"section1": "data1", "section2": "data2", "section3": "data3"}

if __name__ == "__main__":
    # print(chunk_json_string(data, 30))
    # print(embed_to_str(torch.tensor([[1, 2, 3], [4, 5, 6]])))
    emb = torch.tensor([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
    print(emb.tolist())

    print(list(list(i) for i in emb.numpy()))

    # tensor = torch.tensor([[1, 2, 3], [4, 5, 6]])

    # # Convert the tensor to a list
    # python_list = tensor.numpy().tolist()

    # print(python_list)

    query = """
    Patient Information:
        Age: 26
        Gender: Female
        Medical History: No significant past medical issues
        Allergies: None known
        Current Medications: None
    Reported Symptoms: - Migraine
        - Cough
        - Chest Tightness
        - Rash
    """