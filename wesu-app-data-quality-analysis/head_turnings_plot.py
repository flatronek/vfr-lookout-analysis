from vfr_data_analysis.quaterion_utils import *
from vfr_data_analysis.constants_and_utils import *
from vfr_data_analysis.transition_matrix_utils import *
from vfr_data_analysis.ploting import *
from vfr_data_analysis.realTimeDataAnalysis import *
from vfr_data_analysis.samples import *

if __name__ == "__main__":  
    quat = qt_from_two_vectors(args[cmd_arg_accelerationVector], z_axis_vector)
    head_gyr_data = load_data_of(dev_head, cat_gyroscope)
    head_gyr_orient_quaternion_data = orientate_data_using_quaternion(head_gyr_data, quat)
    head_turnings_data = detect_head_turnings(head_gyr_orient_quaternion_data)

    plotDetectionData(head_turnings_data)
    export_head_turnings_to_csv(head_turnings_data)