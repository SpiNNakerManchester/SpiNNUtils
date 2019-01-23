def find_max_success(max_possible, check):
    if check(max_possible):
        return max_possible
    return search_for_max_success(0, max_possible, check)

def search_for_max_success(best_success, min_fail, check):
    if (best_success >= min_fail -1):
        return best_success
    mid_point = (best_success + min_fail) // 2
    if check(mid_point):
        return  search_for_max_success(mid_point, min_fail, check)
    else:
        return  search_for_max_success(best_success, mid_point, check)
