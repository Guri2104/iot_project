import yaml


if __name__ == '__main__':
    with open('bugs.yaml', 'a') as yamlfile:
        config_skeleton = {
            "deviceId": 5,
            "readings": 8
        }
        new_id = 9
        to_append = {new_id: config_skeleton}
        yaml.safe_dump(to_append, yamlfile)  # Also note the safe_dump
    # with open('bugs.yaml') as file:
    #     # The FullLoader parameter handles the conversion from YAML
    #     # scalar values to the Python dictionary format
    #     print(yaml.load(file, Loader=yaml.FullLoader))