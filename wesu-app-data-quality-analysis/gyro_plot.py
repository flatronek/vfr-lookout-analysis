from head_angle import prepareGliderGyroData, head_gyro_calibration_vector
from vfr_data_analysis.realTimeDataAnalysis import *
from vfr_data_analysis.samples import *

# 2017-05-17
head_neutral_acc_vector = pd.np.array([-1000, -125, 170])
glider_neutral_acc_vector = pd.np.array([-200, -54, 970])

# 2017-05-18
# head_neutral_acc_vector = pd.np.array([-825, 556, 90])

def plot(data):
    plotData(data, title="Head gyroscope data")
    plt.show()


def prepare_gyro_data(deviceId, startTimestamp, endTimestamp):
    gyroData = load_data_of(deviceId, cat_gyroscope)

    df = gyroData.df
    timeCutDf = df[(df[file_header_hostTimestamp] > startTimestamp) & (df[file_header_hostTimestamp] < endTimestamp)]

    return Data(gyroData.device, gyroData.category, timeCutDf)


def prepare_gyro_data_orientated(deviceId, neutralAccVector, startTimestamp, endTimestamp):
    gyroData = load_data_of(deviceId, cat_accelerometer)

    reorientVector = qt_from_two_vectors(neutralAccVector, z_axis_vector)
    orientGyrData = orientate_data_using_quaternion(gyroData, reorientVector)

    df = orientGyrData.df
    timeCutDf = df[(df[file_header_hostTimestamp] > startTimestamp) & (df[file_header_hostTimestamp] < endTimestamp)]

    return Data(gyroData.device, gyroData.category, timeCutDf)


def run():
    startTime = 0
    endTime = 3000000

    head_acc_data = prepareGliderGyroData(dev_head, head_neutral_acc_vector, head_gyro_calibration_vector,
                                          startTime, endTime)
    # head_acc_data = prepare_gyro_data(dev_head, startTime, endTime)
    plot(head_acc_data)


if __name__ == "__main__":
    run()