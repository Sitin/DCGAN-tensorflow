"""
Modification of https://github.com/stanfordnlp/treelstm/blob/master/scripts/download.py

Downloads the following:
- Celeb-A dataset
- LSUN dataset
- MNIST dataset
- Oxford Flowers (17) dataset
- Oxford Flowers (17) simplified dataset
"""

from __future__ import print_function
import os
import sys
import gzip
import json
import shutil
import zipfile
import argparse
import subprocess
import glob
from PIL import Image
from six.moves import urllib

parser = argparse.ArgumentParser(description='Download dataset for DCGAN.')
parser.add_argument('datasets', metavar='N', type=str, nargs='+',
                    choices=['celebA', 'lsun', 'mnist', '17flowers', '17flowers_simplified'],
                    help='name of dataset to download [celebA, lsun, mnist]')

def download(url, dirpath):
  filename = url.split('/')[-1]
  filepath = os.path.join(dirpath, filename)
  u = urllib.request.urlopen(url)
  f = open(filepath, 'wb')
  filesize = int(u.headers["Content-Length"])
  print("Downloading: %s Bytes: %s" % (filename, filesize))

  downloaded = 0
  block_sz = 8192
  status_width = 70
  while True:
    buf = u.read(block_sz)
    if not buf:
      print('')
      break
    else:
      print('', end='\r')
    downloaded += len(buf)
    f.write(buf)
    status = (("[%-" + str(status_width + 1) + "s] %3.2f%%") %
      ('=' * int(float(downloaded) / filesize * status_width) + '>', downloaded * 100. / filesize))
    print(status, end='')
    sys.stdout.flush()
  f.close()
  return filepath

def unzip(filepath):
  print("Extracting: " + filepath)
  dirpath = os.path.dirname(filepath)
  with zipfile.ZipFile(filepath) as zf:
    zf.extractall(dirpath)
  os.remove(filepath)

def download_celeb_a(dirpath):
  data_dir = 'celebA'
  if os.path.exists(os.path.join(dirpath, data_dir)):
    print('Found Celeb-A - skip')
    return
  url = 'https://www.dropbox.com/sh/8oqt9vytwxb3s4r/AADIKlz8PR9zr6Y20qbkunrba/Img/img_align_celeba.zip?dl=1&pv=1'
  filepath = download(url, dirpath)
  zip_dir = ''
  with zipfile.ZipFile(filepath) as zf:
    zip_dir = zf.namelist()[0]
    zf.extractall(dirpath)
  os.remove(filepath)
  os.rename(os.path.join(dirpath, zip_dir), os.path.join(dirpath, data_dir))

def _list_categories(tag):
  url = 'http://lsun.cs.princeton.edu/htbin/list.cgi?tag=' + tag
  f = urllib.request.urlopen(url)
  return json.loads(f.read())

def _download_lsun(out_dir, category, set_name, tag):
  url = 'http://lsun.cs.princeton.edu/htbin/download.cgi?tag={tag}' \
      '&category={category}&set={set_name}'.format(**locals())
  print(url)
  if set_name == 'test':
    out_name = 'test_lmdb.zip'
  else:
    out_name = '{category}_{set_name}_lmdb.zip'.format(**locals())
  out_path = os.path.join(out_dir, out_name)
  cmd = ['curl', url, '-o', out_path]
  print('Downloading', category, set_name, 'set')
  subprocess.call(cmd)

def download_lsun(dirpath):
  data_dir = os.path.join(dirpath, 'lsun')
  if os.path.exists(data_dir):
    print('Found LSUN - skip')
    return
  else:
    os.mkdir(data_dir)

  tag = 'latest'
  #categories = _list_categories(tag)
  categories = ['bedroom']

  for category in categories:
    _download_lsun(data_dir, category, 'train', tag)
    _download_lsun(data_dir, category, 'val', tag)
  _download_lsun(data_dir, '', 'test', tag)

def download_mnist(dirpath):
  data_dir = os.path.join(dirpath, 'mnist')
  if os.path.exists(data_dir):
    print('Found MNIST - skip')
    return
  else:
    os.mkdir(data_dir)
  url_base = 'http://yann.lecun.com/exdb/mnist/'
  file_names = ['train-images-idx3-ubyte.gz',
                'train-labels-idx1-ubyte.gz',
                't10k-images-idx3-ubyte.gz',
                't10k-labels-idx1-ubyte.gz']
  for file_name in file_names:
    url = (url_base+file_name).format(**locals())
    print(url)
    out_path = os.path.join(data_dir,file_name)
    cmd = ['curl', url, '-o', out_path]
    print('Downloading ', file_name)
    subprocess.call(cmd)
    cmd = ['gzip', '-d', out_path]
    print('Decompressing ', file_name)
    subprocess.call(cmd)

def download_17flowers(dirpath):
  data_dir = os.path.join(dirpath, '17flowers')

  if os.path.exists(data_dir):
    print('Found Oxford Flowers - skip')
    return
  else:
    os.mkdir(data_dir)
  url_base = 'http://www.robots.ox.ac.uk/~vgg/data/flowers/17/'
  file_names = ['17flowers.tgz']
  for file_name in file_names:
    url = (url_base+file_name).format(**locals())
    print(url)
    out_path = os.path.join(data_dir,file_name)

    cmd = ['curl', url, '-o', out_path]
    print('Downloading ', file_name)
    subprocess.call(cmd)

    cmd = ['tar', '-zxvf', out_path, '-C', data_dir]
    print('Decompressing ', file_name)
    subprocess.call(cmd)

    print('Resizing')
    new_width = 128
    new_height = 128
    for path in glob.glob(data_dir + '/jpg/*.jpg'):
      img = Image.open(path)
      width, height = img.size   # Get dimensions

      if height > width:
        img = img.resize((new_width, int(new_height * height / width)),
                         Image.ANTIALIAS)
      else:
        img = img.resize((int(new_width * width / height), new_height),
                         Image.ANTIALIAS)

      width, height = img.size   # Get dimensions

      left = (width - new_width)/2
      top = (height - new_height)/2
      right = (width + new_width)/2
      bottom = (height + new_height)/2

      cropped = img.crop((left, top, right, bottom))

      name = os.path.splitext(os.path.basename(path))[0]
      cropped.save(data_dir + '/' + name + '.png')

      print(name)

    cmd = ['rm', '-rf', data_dir + '/jpg', data_dir + '/' + file_name]
    print('Cleaning up ', file_name)
    subprocess.call(cmd)

def download_17flowers_simplified(dirpath):
  data_dir = os.path.join(dirpath, '17flowers_simplified')

  if os.path.exists(data_dir):
    print('Found Oxford Flowers simplified - skip')
    return
  else:
    os.mkdir(data_dir)
  url_base = 'https://dl.dropboxusercontent.com/s/00lml7uxgamm6n9/'
  file_names = ['17flowers_simplified.zip']
  for file_name in file_names:
    url = (url_base+file_name).format(**locals())
    print(url)
    out_path = os.path.join(data_dir,file_name)

    cmd = ['curl', url, '-o', out_path]
    print('Downloading ', file_name)
    subprocess.call(cmd)

    cmd = ['unzip', out_path, '-d', data_dir]
    print('Decompressing ', file_name)
    subprocess.call(cmd)

    cmd = ['rm', data_dir + '/' + file_name]
    print('Cleaning up ', file_name)
    subprocess.call(cmd)

def download_17flowers_simplified_model(dirpath):
  url_base = 'https://dl.dropboxusercontent.com/s/bgdonwya6wlz5g0/'
  file_names = ['17flowers_simplified-models.zip']
  for file_name in file_names:
    url = (url_base+file_name).format(**locals())
    print(url)
    out_path = os.path.join(dirpath,file_name)

    cmd = ['curl', url, '-o', out_path]
    print('Downloading ', file_name)
    subprocess.call(cmd)

    cmd = ['unzip', out_path, '-d', dirpath]
    print('Decompressing ', file_name)
    subprocess.call(cmd)

    cmd = ['rm', out_path]
    print('Cleaning up ', file_name)
    subprocess.call(cmd)

def prepare_data_dir(path = './data'):
  if not os.path.exists(path):
    os.mkdir(path)

if __name__ == '__main__':
  args = parser.parse_args()
  prepare_data_dir()

  if 'celebA' in args.datasets:
    download_celeb_a('./data')
  if 'lsun' in args.datasets:
    download_lsun('./data')
  if 'mnist' in args.datasets:
    download_mnist('./data')
  if '17flowers' in args.datasets:
    download_17flowers('./data')
  if '17flowers_simplified' in args.datasets:
    download_17flowers_simplified('./data')
    download_17flowers_simplified_model('./checkpoint')
