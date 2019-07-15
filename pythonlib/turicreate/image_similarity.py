"""
https://github.com/apple/turicreate
run on IOS, Linux, WSL
https://apple.github.io/turicreate/docs/userguide/image_similarity/
"""
import turicreate as tc

image_folder = 'image'
# load images from dirs
# data is sframe
data = tc.image_analysis.load_images(image_folder, with_path=True)
data = data.add_row_number()
# data.explore()
model = tc.image_similarity.create(data)
# find 10 similarity images
# transfer learning
similar_images = model.query(data[0:1], k=10)
similar_image_index = similar_images['reference_label'][1:]
filtered_index = data['id'].apply(lambda x : x in similar_image_index)
# show the 10 similarity images
data[filtered_index].explore()
