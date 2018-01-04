from vfr_data_analysis.realTimeDataAnalysis import *
from vfr_data_analysis.samples import *


def plotZAxis2(dataFrame1, dataFrame2, label1 = "DF1", label2 = "DF2"):
    x1 = dataFrame1[file_header_real_time]
    values1 = dataFrame1[file_header_Z_dps]

    x2 = dataFrame2[file_header_real_time]
    values2 = dataFrame2[file_header_Z_dps]

    title = "Glider Turnings"

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


def run():
    # cmd_arg_accelerationVector = pd.np.array([-773, 612, 175])
    cmd_arg_accelerationVector = pd.np.array([-1000, -125, 170])

    quat = qt_from_two_vectors(cmd_arg_accelerationVector, z_axis_vector)
    head_gyr_data = load_data_of(dev_head, cat_gyroscope)
    head_gyr_orient_quaternion_data = orientate_data_using_quaternion(head_gyr_data, quat)

    # correctData = head_gyr_orient_quaternion_data.df[head_gyr_orient_quaternion_data.df[file_header_hostTimestamp] > 530000]

    # data in between 17:07:05 - 17:07:15 - 1 full head turn
    correctData = head_gyr_orient_quaternion_data.df[(head_gyr_orient_quaternion_data.df[file_header_hostTimestamp] > 550000) & (head_gyr_orient_quaternion_data.df[file_header_hostTimestamp] < 568000)]
    print("All data size: %d, correct data size: %d" % (len(head_gyr_orient_quaternion_data.df.index), len(correctData.index)))

    interpolatedData = interpolate_data(Data(head_gyr_orient_quaternion_data.device, head_gyr_orient_quaternion_data.category, correctData), 10)
    # interpolatedData = Data(head_gyr_orient_quaternion_data.device, head_gyr_orient_quaternion_data.category, correctData)
    plotZAxis2(correctData, interpolatedData.df, "Non interpolated", "Interpolated")

    zDps = np.array(interpolatedData.df[file_header_Z_dps])
    print(zDps)
    print("Negative zDPS sum: %d" % sum(zDps[zDps < 0]))
    print("Non negative zDPS sum: %d" % sum(zDps[zDps >= 0]))


    z = interpolatedData.df[file_header_Z_dps]
    t = interpolatedData.df[file_header_hostTimestamp]
    z_cum_int = integrate.cumtrapz(z, t / 1000, initial=0)
    fig, ax = plt.subplots()
    fig.set_size_inches(24.4, 6)
    plt.title("Cumulative trapez integration")
    # ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
    plt.grid()
    plt.plot(t, z_cum_int, marker='.', linestyle='--')
    plt.show()


if __name__ == "__main__":
    run()