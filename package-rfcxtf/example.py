import rfcxtf

model_path = './example/model'
audio_path = './example/guardian_audio.wav'

model = rfcxtf.ClassifierTF2(model_path)
print('Model loaded')
print(' - class names =', model.class_names)
print(' - sample rate =', model.sample_rate)
print(' - window duration =', model.window_duration, 'secs')
print(' - window step =', model.window_step, 'secs')

scores = model.score(audio_path)
print('\nScoring complete')
for class_name in model.class_names:
    score = ["{:.4f}".format(s) for s in scores[class_name]]
    if len(score) > 6:
        score_txt = f'{score[0]}, {score[1]}, {score[2]}, ..., {score[-3]}, {score[-2]}, {score[-1]}'
    else:
        score_txt = ', '.join(score)
    print(f' - {class_name} [{score_txt}] ({len(score)} values)')

min_confidence = 0.55
print(f'\nWindows above threshold {min_confidence}')
for class_name in model.class_names:
    filtered_score_indexes = []
    for i, value in enumerate(scores[class_name]):
        if value > min_confidence:
            filtered_score_indexes.append(i)
    if len(filtered_score_indexes) == 0:
        print(' -', class_name, 'none')
    else:
        filtered_score_indexes_txt = [f'{"{:.1f}".format(s * model.window_step)}s' for s in filtered_score_indexes]
        print(' -', class_name, 'at', ', '.join(filtered_score_indexes_txt))
