from vfr_data_analysis.realTimeDataAnalysis import *
from vfr_data_analysis.samples import *


head_neutral_acc_vector = pd.np.array([-1000, -125, 170])
glider_neutral_acc_vector = pd.np.array([-200, -54, 970])

head_gyro_calibration_vector = pd.np.array([0.4, -0.9, -1.6])
glider_gyro_calibration_vector = pd.np.array([1.6, -3.6, -3.3])


def plotZAxis(dataFrame1, title = "Gyroscope data"):
    x1 = dataFrame1[file_header_real_time]
    values1 = dataFrame1[file_header_Z_dps]

    fig, ax = plt.subplots()
    fig.canvas.set_window_title(title)
    # fig.set_size_inches(24.4, 6)
    fig.set_size_inches(21, 9)
    plt.title(title)
    plt.gcf().autofmt_xdate()

    plt.plot(x1, values1, marker='.', linestyle='--')

    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
    plt.grid()
    plt.legend(["Z-axis"])
    plt.show()


def plotZAxis2(dataFrame1, dataFrame2, label1="DF1", label2="DF2"):
    x1 = dataFrame1[file_header_real_time]
    values1 = dataFrame1[file_header_Z_dps]

    x2 = dataFrame2[file_header_real_time]
    values2 = dataFrame2[file_header_Z_dps]

    title = "Head gyroscope data"

    fig, ax = plt.subplots()
    fig.canvas.set_window_title(title)
    # fig.set_size_inches(24.4, 6)
    fig.set_size_inches(21, 9)
    plt.title(title)
    plt.gcf().autofmt_xdate()

    plt.plot(x1, values1, marker='.', linestyle='--')
    plt.plot(x2, values2, marker='.', linestyle='--')

    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
    plt.grid()
    plt.legend([label1, label2])
    plt.show()


def prepareGliderGyroData(deviceId, neutralAccVector, axisCalibrationVector, startTimestamp, endTimestamp):
    reorientVector = qt_from_two_vectors(neutralAccVector, z_axis_vector)

    loadedGyrData = load_data_of(deviceId, cat_gyroscope)

    calibratedGyrData = calibrateDataAxis(loadedGyrData, axisCalibrationVector)

    orientGyrData = orientate_data_using_quaternion(calibratedGyrData, reorientVector)

    df = orientGyrData.df
    timeCutDf = df[(df[file_header_hostTimestamp] > startTimestamp) & (df[file_header_hostTimestamp] < endTimestamp)]

    return Data(orientGyrData.device, orientGyrData.category, timeCutDf)


def interpolateDatas(data1, data2):
    startTimestamp = max(data1.df[file_header_hostTimestamp].iloc[0], data2.df[file_header_hostTimestamp].iloc[0])
    endTimestamp = max(data1.df[file_header_hostTimestamp].iloc[-1], data2.df[file_header_hostTimestamp].iloc[-1])

    print("Start timestamp is %d, end timestamp is %d" % (startTimestamp, endTimestamp))

    interpolatedData = interpolate_data(data1, 10, startTimestamp, endTimestamp)

    print("Pre interp")
    print(data1.df.iloc[0:10])
    print("Interpolated data start: \n")
    print(interpolatedData.df.iloc[0:10])

    print("Interp data size is %d" % len(interpolatedData.df.index))
    return interpolatedData


def calibrateDataAxis(data, calibrationVector):
    result = copy.deepcopy(data)

    result.df[result.df.columns[5]] = result.df[result.df.columns[5]] - calibrationVector[0]
    result.df[result.df.columns[6]] = result.df[result.df.columns[6]] - calibrationVector[1]
    result.df[result.df.columns[7]] = result.df[result.df.columns[7]] - calibrationVector[2]

    return result


def cumulateAndPlotData(gliderData, headData):
    gliderTime = gliderData.df[file_header_hostTimestamp]
    headTime = headData.df[file_header_hostTimestamp]

    headZAxis = headData.df[file_header_Z_dps]
    gliderZAxix = gliderData.df[file_header_Z_dps]

    headIntegratedData = integrate.cumtrapz(headZAxis, headTime / 1000, initial=0)
    gliderIntegratedData = integrate.cumtrapz(gliderZAxix, gliderTime / 1000, initial=0)

    fig, ax = plt.subplots()
    fig.set_size_inches(24.4, 6)

    plt.plot(headTime, headIntegratedData, marker='.', linestyle='--')
    plt.plot(gliderTime, gliderIntegratedData, marker='.', linestyle='--')
    plt.plot(headTime, headIntegratedData - gliderIntegratedData, marker='.', linestyle='--')

    plt.title("Cumulative trapeze integration")
    # ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
    plt.grid()
    plt.legend(["Head data", "Glider data", "Result"])
    plt.show()


def run():
    startTime = 550000
    endTime = 800000

    gliderTimeCutData = prepareGliderGyroData(dev_glider, glider_neutral_acc_vector, glider_gyro_calibration_vector, startTime, endTime)
    headTimeCutData = prepareGliderGyroData(dev_head, head_neutral_acc_vector, head_gyro_calibration_vector, startTime, endTime)

    gliderInterpolatedData = interpolateDatas(gliderTimeCutData, headTimeCutData)
    headInterpolatedData = interpolateDatas(headTimeCutData, gliderTimeCutData)

    plotZAxis(headInterpolatedData.df, "Head gyro data")

    cumulateAndPlotData(gliderInterpolatedData, headInterpolatedData)


if __name__ == "__main__":
    run()
