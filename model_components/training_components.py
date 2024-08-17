def get_most_freq_move(data):

    dup_count_df = data.groupby(["State","Move"]).transform("size").rename("Dup_Count")
    data = data.join(dup_count_df)
    data = data.drop_duplicates()

    max_idx = data.groupby(["State"])["Dup_Count"].transform("max") == data["Dup_Count"]
    data = data[max_idx]
    data = data.drop(["Dup_Count"], axis=1)
    return data
