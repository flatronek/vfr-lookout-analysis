from vfr_data_analysis.realTimeDataAnalysis import *
from vfr_data_analysis.samples import *

# 2017-05-17
head_neutral_acc_vector = pd.np.array([-1000, -125, 170])
glider_neutral_acc_vector = pd.np.array([-200, -54, 970])


def plot(data):
    plotData(data)
    plt.show()


def prepare_magnetometer_data_orientated(deviceId, neutralAccVector, startTimestamp, endTimestamp):
    reorientVector = qt_from_two_vectors(neutralAccVector, z_axis_vector)

    magData = load_data_of(deviceId, cat_magnetometer)
    filteredData = filter_out_spikes(magData)

    orientGyrData = orientate_data_using_quaternion(filteredData, reorientVector)

    df = orientGyrData.df
    timeCutDf = df[(df[file_header_hostTimestamp] > startTimestamp) & (df[file_header_hostTimestamp] < endTimestamp)]

    return Data(orientGyrData.device, orientGyrData.category, timeCutDf)


def prepare_magnetometer_data(deviceId, startTimestamp, endTimestamp):
    magData = load_data_of(deviceId, cat_magnetometer)
    filteredData = filter_out_spikes(magData)

    df = filteredData.df
    timeCutDf = df[(df[file_header_hostTimestamp] > startTimestamp) & (df[file_header_hostTimestamp] < endTimestamp)]

    return Data(filteredData.device, filteredData.category, timeCutDf)


def run():
    startTime = 550000
    endTime = 800000

    head_mag_data = prepare_magnetometer_data(dev_head, startTime, endTime)
    plot(head_mag_data)


if __name__ == "__main__":
    run()
