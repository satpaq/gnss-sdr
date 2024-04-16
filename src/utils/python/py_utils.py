import os
import re
import pytest

''' tools for python stuff '''

def create_directory(path):
    if os.path.exists(path):
        os.rmdir(path)
    os.makedirs(path)

@pytest.mark.parametrize("file_path, dir_name", [
    ("work/mini_0718_4m_bruce_lna_t2.dat", "mini_0718_4m_bruce_lna_t2"),
    ("work/usrp_mini_60s_4m_f.dat", "usrp_mini_60s_4m_f")
    # Add more test cases as needed
])
def extract_trial_name(file_path: str) -> str:
    ''' extract the name of the raw data file grabbed by usrp ending 
    in .dat to be used for processing file output dir

    Arguments:
        file_path: the relative path of the input raw data
    Returns:
        output_name: the name of the test trial to use as an output dir
    '''
    name_match = re.search(r'work\/(.*?)\.dat$', file_path)
    output_name = name_match.group(1) if name_match else None
    return output_name.lower()

@pytest.mark.parametrize("conf_path, parent_name", [
    ("work/gnss-sdr_GPS_L1_darren.conf", "darren"),
    ("work/gnss-sdr_GPS_L1_spain.conf", "spain")
    # Add more test cases as needed
])
def extract_conf_type(conf_path) -> str:
    ''' extract the name of the conf type used for this rcvr run

    Arguments:
        conf_path: the relative path of the input raw data
    Returns:
        conf_name: the name of the test trial to use as an output dir
    '''# Extract A - the conf rcvr type run - to becomee the parent dir
    conf_match = re.search(r'_([^_]*)\.conf$', conf_path)
    conf_name = conf_match.group(1) if conf_match else None
    return conf_name.lower()

@pytest.mark.parametrize("conf_file, dat_file, expected_dir", [
    ("work/gnss-sdr_GPS_L1_darren.conf", "work/mini_0718_4m_bruce_lna_t2.dat", "data/darren/mini_0718_4m_bruce_lna_t2"),
    # Add more test cases as needed
])
def test_directory_creation(conf_file, dat_file, expected_dir):
    A = extract_conf_type(conf_file)
    B = extract_trial_name(dat_file)
    
    if A and B:
        new_directory = os.path.join("data", A, B)
        create_directory(new_directory)
        assert new_directory == expected_dir
    else:
        pytest.fail("Failed to extract A and/or B from file paths.")


if __name__ == "__main__":
    pytest.main([__file__])
