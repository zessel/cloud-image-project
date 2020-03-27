from django.shortcuts import render
from django.template import RequestContext
from myapp.forms import UploadFileForm
from PIL import Image, ImageOps,ImageFilter
from imagepro.settings import BASE_DIR
#from . import s3upload
import boto3

conn = boto3.resource('s3')
bucketname = 'tuk01401-4517-project1-imagebucket'

def applyfilter(filename, preset):
	
	inputfile = BASE_DIR + '/media/' + filename

	f=filename.split('.')
	outputfilename = f[0] + '-out.jpg'

	outputfile = BASE_DIR + '/myapp/templates/static/output/' + outputfilename

	im = Image.open(inputfile)
	if preset=='gray':
		im = ImageOps.grayscale(im)

	if preset=='edge':
		im = ImageOps.grayscale(im)
		im = im.filter(ImageFilter.FIND_EDGES)

	if preset=='poster':
		im = ImageOps.posterize(im,3)

	if preset=='solar':
		im = ImageOps.solarize(im, threshold=80) 

	if preset=='blur':
		im = im.filter(ImageFilter.BLUR)
	
	if preset=='sepia':
		sepia = []
		r, g, b = (239, 224, 185)
		for i in range(255):
			sepia.extend((r*i//255, g*i//255, b*i//255))
		im = im.convert("L")
		im.putpalette(sepia)
		im = im.convert("RGB")

	im.save(outputfile)
	data = open(outputfile, 'rb') 
	conn.Bucket(bucketname).put_object(Key=outputfilename, Body=data, ACL='public-read')
	return outputfilename

def handle_uploaded_file(f,preset):
	bucketname = 'tuk01401-4517-project1-imagebucket'
	uploadfilename='media/' + f.name
	with open(uploadfilename, 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)

	outputfilename=applyfilter(f.name, preset)
	data = open(uploadfilename, 'rb')
	conn.Bucket(bucketname).put_object(Key=f.name, Body=data, ACL='public-read')
	#upload_to_s3_bucket_root(bucketname, f.name)
	#upload_to_s3_bucket_root(bucketname, outputfilename)
	return outputfilename

def home(request):
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			preset=request.POST['preset']
			outputfilename = handle_uploaded_file(request.FILES['myfilefield'],preset)
			return render(request, 'process.html',{'outputfilename': outputfilename})
	else:
		form = UploadFileForm() 
	return render(request, 'index.html',{'form': form})

def process(request):
	return render(request, 'process.html', {})


def upload_to_s3_bucket_root(bucketname, filename):
	#conn.upload_file(filename, bucketname, None)
	#mybucket = conn.Bucket(bucketname)
	#data = open(filename, 'rb')
	#mybucket.put_object(Key=filename,Body=data)
	return 1
