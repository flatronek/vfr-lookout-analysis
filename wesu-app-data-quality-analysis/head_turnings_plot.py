from head_angle import prepareGliderGyroData, head_gyro_calibration_vector, plotZAxis
from vfr_data_analysis.realTimeDataAnalysis import *
from vfr_data_analysis.samples import *

# 2017-05-17
head_neutral_acc_vector = pd.np.array([-1000, -125, 170])
glider_neutral_acc_vector = pd.np.array([-200, -54, 970])

def loadData(filename, dateColName):
    try:
        df = pd.DataFrame.from_csv(filename, index_col=False, parse_dates=[dateColName])
        return df
    except FileNotFoundError:
        print("!!!!!!", filename, "not present in current directory!!!!!!")


def run():
    startTime = 550000
    endTime = 800000

    headGyroData = prepareGliderGyroData(dev_head, head_neutral_acc_vector, head_gyro_calibration_vector,
                                          startTime, endTime)
    headDetectionData = detect_head_turnings(headGyroData)

    plotZAxis(headGyroData.df, title="Head gyroscope data (orientated)")

    plotDetectionData(headDetectionData)


if __name__ == "__main__":
    run()
    # quat = qt_from_two_vectors(args[cmd_arg_accelerationVector], z_axis_vector)
    # head_gyr_data = load_data_of(dev_head, cat_gyroscope)
    # head_gyr_orient_quaternion_data = orientate_data_using_quaternion(head_gyr_data, quat)
    # head_turnings_data = detect_head_turnings(head_gyr_orient_quaternion_data)
    #
    # plotDetectionData(head_turnings_data)
    # export_head_turnings_to_csv(head_turnings_data)
