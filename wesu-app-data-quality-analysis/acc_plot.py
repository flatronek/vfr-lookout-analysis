from vfr_data_analysis.realTimeDataAnalysis import *
from vfr_data_analysis.samples import *

# 2017-05-17
# head_neutral_acc_vector = pd.np.array([-1000, -125, 170])
glider_neutral_acc_vector = pd.np.array([-200, -54, 970])

# 2017-05-18
head_neutral_acc_vector = pd.np.array([-875, 462, 82])

def plot(data):
    plotData(data, title="Head accelerometer data (orientated)")
    plt.show()


def prepare_magnetometer_data_orientated(deviceId, neutralAccVector, startTimestamp, endTimestamp):
    reorientVector = qt_from_two_vectors(neutralAccVector, z_axis_vector)

    magData = load_data_of(deviceId, cat_magnetometer)
    filteredData = filter_out_spikes(magData)

    orientGyrData = orientate_data_using_quaternion(filteredData, reorientVector)

    df = orientGyrData.df
    timeCutDf = df[(df[file_header_hostTimestamp] > startTimestamp) & (df[file_header_hostTimestamp] < endTimestamp)]

    return Data(orientGyrData.device, orientGyrData.category, timeCutDf)


def prepare_accelerometer_data(deviceId, startTimestamp, endTimestamp):
    magData = load_data_of(deviceId, cat_accelerometer)
    filteredData = magData

    df = filteredData.df
    timeCutDf = df[(df[file_header_hostTimestamp] > startTimestamp) & (df[file_header_hostTimestamp] < endTimestamp)]

    return Data(filteredData.device, filteredData.category, timeCutDf)


def prepare_accelerometer_data_orientated(deviceId, neutralAccVector, startTimestamp, endTimestamp):
    accData = load_data_of(deviceId, cat_accelerometer)

    reorientVector = qt_from_two_vectors(neutralAccVector, z_axis_vector)
    orientGyrData = orientate_data_using_quaternion(accData, reorientVector)

    df = orientGyrData
    timeCutDf = df[(df[file_header_hostTimestamp] > startTimestamp) & (df[file_header_hostTimestamp] < endTimestamp)]

    return Data(accData.device, accData.category, timeCutDf)


def run():
    startTime = 0
    endTime = 3000000

    # head_acc_data = prepare_accelerometer_data_orientated(dev_head, head_neutral_acc_vector, startTime, endTime)
    head_acc_data = prepare_accelerometer_data(dev_head, startTime, endTime)
    plot(head_acc_data)


if __name__ == "__main__":
    run()
