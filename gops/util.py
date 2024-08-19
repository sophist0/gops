def get_model_base_name(NUM_EPOCHS, model_version, train_device, tokenizer):
    return str(NUM_EPOCHS) + "_v" + str(model_version) + "_" + str(train_device) + "_" + tokenizer

def get_path_names(NUM_EPOCHS, model_version, train_device, tokenizer):

    base_name = get_model_base_name(NUM_EPOCHS, model_version, train_device, tokenizer)
    app_paths = {}
    app_paths["state_tokenizer_path"] = "models/" + base_name + "_state_tokenizer.json"
    app_paths["move_tokenizer_path"] = "models/" + base_name + "_move_tokenizer.json"
    app_paths["model_path"] = "models/epoch_" + base_name
    app_paths["train_data_path"] = "models/train_data_" + base_name + ".npy"
    return app_paths


