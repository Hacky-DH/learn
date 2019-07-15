"""
https://github.com/apple/turicreate
run on IOS, Linux, WSL
from https://apple.github.io/turicreate/docs/userguide/image_classifier/
"""
import turicreate as tc

image_folder = 'image'
# load images from dirs
# data is sframe
data = tc.image_analysis.load_images(image_folder, with_path=True)
print_rows(num_rows=10)
# add labels
data['label'] = data['path'].apply(lambda path: 'one' if 'one' in path
	else 'two' if 'two' in path else 'three')
data.save('images.sframe')
# data.explore()
train_data, test_data = data.random_split(0.8, seed=2)
# train the model
model = tc.image_classifier.create(train_data, target='label', model='squeezenet_v1.1')
# predict
predictions = model.predict(test_data)
metrics = model.evaluate(test_data)
print(metrics['accuracy'])
wrong_pred_img_path = test_data[predictions != test_data['label']][0]['path']
img = tc.Image(wrong_pred_img_path)
img.show()
# export to CoreML
model.export_coreml('test1.mlmodel')
