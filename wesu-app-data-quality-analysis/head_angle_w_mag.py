from head_angle import *
from magnetometer_plot import *


def plotAll(headData, gliderData, headRelData, magData):
    fig, ax = plt.subplots()
    fig.set_size_inches(24.4, 6)

    plt.plot(headData.df[file_header_hostTimestamp], headData.df[file_header_Z_dps], marker='.', linestyle='--')
    plt.plot(gliderData.df[file_header_hostTimestamp], gliderData.df[file_header_Z_dps], marker='.', linestyle='--')
    plt.plot(headRelData.df[file_header_hostTimestamp], headRelData.df[file_header_Z_dps], marker='.', linestyle='--')

    # columns [5:] are magnetometers X,Y,Z axis values
    mag_values_labels = list(magData.df.columns)[5:]
    for label in mag_values_labels:
        values = list(magData.df[label])
        plt.plot(magData.df[file_header_hostTimestamp], values, marker='.', linestyle='--')

    plt.title("Cumulative trapeze integration")
    # ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
    plt.grid()
    plt.legend(["Head angle", "Glider angle", "Head relative"] + mag_values_labels)
    plt.show()


def run():
    startTime = 550000
    endTime = 800000

    gliderTimeCutData = prepareGliderGyroData(dev_glider, glider_neutral_acc_vector, glider_gyro_calibration_vector,
                                              startTime, endTime)
    headTimeCutData = prepareGliderGyroData(dev_head, head_neutral_acc_vector, head_gyro_calibration_vector,
                                            startTime, endTime)
    headMagData = prepare_magnetometer_data(dev_head, startTime, endTime)

    gliderInterpolatedData = interpolateDatas(gliderTimeCutData, headTimeCutData)
    headInterpolatedData = interpolateDatas(headTimeCutData, gliderTimeCutData)

    gliderAngleData = cumulateZAxisData(gliderInterpolatedData)
    headAngleData = cumulateZAxisData(headInterpolatedData)

    headRelativeAngle = getHeadRelativeAngle(headInterpolatedData, gliderInterpolatedData)

    plotAll(headAngleData, gliderAngleData, headRelativeAngle, headMagData)


if __name__ == "__main__":
    run()
