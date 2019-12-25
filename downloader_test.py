from classes import downloader, metadata, parameter_init

input_name = "./test_input_files/test_input.text"

dw = downloader.Downloader(input_path = input_name)
dw.add_token(token = parameter_init.token_path)
dw.start_download(
    dt = parameter_init.dt, 
    saving_directory = parameter_init.saving_directory, 
    components = parameter_init.components, 
    channels = parameter_init.channels, 
    max_gap = parameter_init.max_gap, 
    data_percentage = parameter_init.data_percentage,
    sleep_time = parameter_init.sleep_time, 
    attempts = parameter_init.attempts,
    override = parameter_init.override,
    processing = parameter_init.processing,
    timedomain_normalization = parameter_init.timedomain_normalization,
    resample = parameter_init.resample,
    sampling_freq = parameter_init.sampling_freq,
    detrend_option = parameter_init.detrend_option,
    anti_aliasing_filter= parameter_init.anti_aliasing_filter,
    filter_order = parameter_init.filter_order,
    zero_phase = parameter_init.zero_phase,
    filters = parameter_init.filters,
    envsmooth = parameter_init.envsmooth,
    env_exp = parameter_init.env_exp,
    min_weight = parameter_init.min_weight,
    taper_length_normalization = parameter_init.taper_length_tdn,
    plot = parameter_init.plot,
    apply_broadband_filter = parameter_init.apply_broadband_filter,
    broadband_filter = parameter_init.broadband_filter,
    apply_whitening = parameter_init.apply_whitening,
    spectrumexp = parameter_init.spectrumexp,
    espwhitening = parameter_init.espwhitening,
    taper_length_whitening = parameter_init.taper_length_whitening
)