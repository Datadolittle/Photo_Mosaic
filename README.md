# Photo_Mosaic
A repository to create photo mosaics using python3




The photo mosaic program requires Pillow and numpy to process the images and matrix manipulation respectively. 

**Install Pillow & numpy**

```
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade Pillow
python3 -m pip install numpy
```


**Test Background Images for 3 Channels**
The mosaic creator will only work for jpeg or jpg formats. This script checks for the proper format and moves unusable images to a new folder. 

```
python Image_Tester.py --images Trees --move
```

**Create Mosaic**

```
python Mosaic_Creator.py --target Tree.jpg --images Trees --grid 100 100
```

