import tornado.ioloop
import tornado.web
import os, random, string
from PIL import Image
import datetime
import io
from bson.objectid import ObjectId
from pymongo import MongoClient


client = MongoClient()

image_db = client.image_db
images_collection = image_db.images_collection

class BaseHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

class UploadImageHandler(BaseHandler):
    def post(self):
        file1 = self.request.files['file1'][0]
        original_fname = file1['filename']
        extension = os.path.splitext(original_fname)[1]
        fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))
        final_filename= fname+extension
        is_valid = False
        while not is_valid:
            if not images_collection.find_one({"filename" : final_filename}):
                is_valid = True

        output_file = open("uploads/" + final_filename, 'wb')
        output_file.write(file1['body'])
        image_descriptor = {
            "filename": final_filename,
            "uploaded_at": datetime.datetime.utcnow(),
            "boxes" : [],
            "treated" : False
        }
        images_collection.insert_one(image_descriptor)
        self.finish("file " + final_filename + " is uploaded")

class GetImageIdHandler(BaseHandler):
    def get(self):
        item = images_collection.aggregate([
                { "$match": { "treated": False } },
                { "$sample": { "size": 1 } }
                ]).next()
        self.finish(str(item['_id']))

class GetImageFileHandler(BaseHandler):
    def get(self, image_id):
        item = images_collection.find_one(
            {"_id" : ObjectId(image_id)}
        )
        fimg = Image.open('./uploads/' +item['filename'])
        imgByteArr = io.BytesIO()
        fimg.save(imgByteArr, format='JPEG')
        self.write(imgByteArr.getvalue())
        self.set_header("Content-type",  "image/jpg")

class ImageFileParserHandler(BaseHandler):
    def post(self, image_id):
        item = images_collection.find_one(
            {"_id" : ObjectId(image_id)}
        )
        fimg = Image.open('./uploads/' +item['filename'])
        imgByteArr = io.BytesIO()
        fimg.save(imgByteArr, format='JPEG')
        self.write(imgByteArr.getvalue())
        self.set_header("Content-type",  "image/jpg")

def make_app():
    return tornado.web.Application([
        (r"/upload_image", UploadImageHandler),
        (r"/get_random_id", GetImageIdHandler),
        (r"/images/([^/]+)", GetImageFileHandler)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()