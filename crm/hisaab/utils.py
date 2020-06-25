def cal_total_transfer(manual, auto):
    total_transfer = manual + auto
    return total_transfer


def cal_total_sale(opening, total_trans, closing):
    total = opening + total_trans - closing
    return total


def cal_comm_value(total_sale, comm=4):
    commission = round(total_sale * (comm / 100)) - 1
    return commission


def cal_net_sale(total_sale, comm_value):
    net_sale = total_sale - comm_value
    return net_sale


def cal_latest_debt(net_sale, last_debt, amt_received):
    latest_debt = net_sale + last_debt - amt_received
    return latest_debt
