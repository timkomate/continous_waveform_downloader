from classes import downloader, metadata, parameter_init

input_name = "./test_input_files/test_input.text"

dw = downloader.Downloader(input_path = input_name)
dw.add_token(token = parameter_init.token_path)
dw.start_download(
            dt = parameter_init.dt,
            components = parameter_init.components,
            channels = parameter_init.channels,
            max_gap = parameter_init.max_gap,
            data_percentage = parameter_init.data_percentage, 
            sleep_time = parameter_init.sleep_time, 
            attempts = parameter_init.attempts
        )
