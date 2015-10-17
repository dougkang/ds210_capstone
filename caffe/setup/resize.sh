for name in /path/to/imagenet/val/*.JPEG; do
    convert -resize 256x256\! $name $name
done


/Users/maktrix/Dropbox/Berkeley/W210_Capstone/ILSVRC2012_img_train_t3