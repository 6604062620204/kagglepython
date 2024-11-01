import h5py
import numpy as np
from PIL import Image
import io

def convertHDF5ToJpg(hdf5Ref, saveTo):
    # สร้างชื่อไฟล์ที่บันทึกเป็นชื่อของ dataset ที่เลือก
    result = f'D:\\KMUTNB-CS\\OOPject\\comfile\\foldercopy\\trainfrompy\\{saveTo}.jpg'
    
    with h5py.File(hdf5Ref, 'r') as f:
        # ตรวจสอบว่า dataset ที่ต้องการมีอยู่ในไฟล์ HDF5 หรือไม่
        if saveTo in f:
            dataset = f[saveTo]
            
            # ตรวจสอบว่าข้อมูลเป็น scalar หรือไม่
            if dataset.ndim == 0:  # Scalar dataset
                data = dataset[()]  # อ่านค่าของ scalar dataset
                print(f"Dataset '{saveTo}' is a scalar dataset with value: {data}")
                # แปลง data ที่เป็น scalar เป็นภาพในที่นี้ต้องปรับตามชนิดข้อมูลของคุณ
                # เช่น ถ้าข้อมูลเป็นภาพสามารถเปลี่ยนเป็น byte array เพื่อเปิดภาพ
                img = Image.open(io.BytesIO(data))  # เปิดภาพจาก bytes
                img.save(result, 'jpeg')
            else:  # Dataset ที่มีมิติ
                data = dataset[:]
                data_normalized = ((data - data.min()) / (data.max() - data.min()) * 255).astype(np.uint8)
                img = Image.fromarray(data_normalized)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(result, 'jpg')
                
            print(f"Image saved as: {result}")
        else:
            print(f"Dataset '{saveTo}' does not exist in the HDF5 file.")

# Usage Here!
hdf5Ref = r'D:\KMUTNB-CS\OOPject\comfile\foldercopy\train-image.hdf5'

# ฟังก์ชันสำหรับพิมพ์ชื่อ dataset ที่พบในไฟล์ HDF5
def print_datasets(name, obj):
    if isinstance(obj, h5py.Dataset):
        datasets.append(name)  # เพิ่มชื่อ dataset ลงในรายการ

# ฟังก์ชันสำหรับลิสต์ชื่อ dataset ทั้งหมดในไฟล์ HDF5
def list_datasets(hdf5Ref):
    with h5py.File(hdf5Ref, 'r') as f:
        f.visititems(print_datasets)

# สร้างรายการสำหรับเก็บชื่อ dataset
datasets = []

# แสดงรายการ dataset ในไฟล์ HDF5
print("Available datasets:")
list_datasets(hdf5Ref)

# Loop ผ่านทุก dataset และแปลงเป็น JPG
for saveTo in datasets:
    convertHDF5ToJpg(hdf5Ref, saveTo)
