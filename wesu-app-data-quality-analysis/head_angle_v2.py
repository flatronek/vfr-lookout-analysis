from vfr_data_analysis.realTimeDataAnalysis import *
from vfr_data_analysis.samples import *


head_neutral_acc_vector = pd.np.array([-1000, -125, 170])
glider_neutral_acc_vector = pd.np.array([-200, -54, 970])


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


def prepareGliderGyroData(deviceId, neutralAccVector, startTimestamp, endTimestamp):
    reorientVector = qt_from_two_vectors(neutralAccVector, z_axis_vector)
    loadedGyrData = load_data_of(deviceId, cat_gyroscope)
    orientGyrData = orientate_data_using_quaternion(loadedGyrData, reorientVector)

    df = orientGyrData.df
    timeCutDf = df[(df[file_header_hostTimestamp] > startTimestamp) & (df[file_header_hostTimestamp] < endTimestamp)]

    interpolatedData = interpolate_data(Data(orientGyrData.device, orientGyrData.category, timeCutDf), 50)

    return interpolatedData


def cumulateAndPlotData(gliderData, headData):
    time = gliderData.df[file_header_hostTimestamp]

    headZAxis = headData.df[file_header_Z_dps]
    gliderZAxix = gliderData.df[file_header_Z_dps]

    headIntegratedData = integrate.cumtrapz(headZAxis, time / 1000, initial=0)
    gliderIntegratedData = integrate.cumtrapz(gliderZAxix, time / 1000, initial=0)

    fig, ax = plt.subplots()
    fig.set_size_inches(24.4, 6)

    plt.plot(time, headIntegratedData, marker='.', linestyle='--')
    plt.plot(time, gliderIntegratedData, marker='.', linestyle='--')

    plt.title("Cumulative trapeze integration")
    # ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
    plt.grid()
    plt.legend(["Head data", "Glider data"])
    plt.show()


def run():
    startTime = 550000
    endTime = 1000000

    gliderInterpolatedData = prepareGliderGyroData(dev_glider, glider_neutral_acc_vector, startTime, endTime)
    headInterpolatedData = prepareGliderGyroData(dev_head, head_neutral_acc_vector, startTime, endTime)
    plotZAxis(gliderInterpolatedData.df, "Head gyro data")

    cumulateAndPlotData(gliderInterpolatedData, headInterpolatedData)


if __name__ == "__main__":
    run()
