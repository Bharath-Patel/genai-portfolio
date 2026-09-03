def summarize_audit_log(logs):
    counting_dict = {}
    for log in logs:
        status = log[4]
        if status in counting_dict:
            counting_dict[status] += 1
        else:
            counting_dict[status] = 1
    return counting_dict