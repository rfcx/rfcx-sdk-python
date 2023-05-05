import numpy as np

def map_to_classes(score_values, class_names):
    results = {}
    for i, class_name in enumerate(class_names):
        results[class_name] = np.zeros(len(score_values[0]), np.float)
        for k, tuple in enumerate(score_values[0]):
            results[class_name][k] = tuple[i]
    return results
