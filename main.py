import h5py
import numpy as np
from PIL import Image
import io
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import os

app = FastAPI()

# ตั้งค่า CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ระบุ URL ของ front-end Svelte ที่จะเข้าถึง API นี้
    allow_credentials=True,
    allow_methods=["*"],  # อนุญาตทุก method เช่น GET, POST
    allow_headers=["*"],   # อนุญาตทุก headers
)

hdf5Folder = r'D:\KMUTNB-CS\OOPject\comfile\foldercopy'

class DatasetRequest(BaseModel):
    filename: str
    datasetNames: List[str]

def convertHDF5ToJpg(hdf5Ref: str, saveTo: str):
    result = os.path.join(hdf5Folder, f'changepicture\\{saveTo}.jpg')

    with h5py.File(hdf5Ref, 'r') as f:
        if saveTo in f:
            dataset = f[saveTo]
            if dataset.ndim == 0:
                data = dataset[()]
                try:
                    img = Image.open(io.BytesIO(data)) 
                    img.save(result, 'jpeg')
                except Exception as e:
                    print(f"Error converting scalar dataset to image: {e}")
            else:
                data = dataset[:]
                data_normalized = ((data - data.min()) / (data.max() - data.min()) * 255).astype(np.uint8)
                img = Image.fromarray(data_normalized)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(result, 'jpg')
                
            print(f"Image saved as: {result}")
        else:
            print(f"Dataset '{saveTo}' does not exist in the HDF5 file.")

def list_datasets(hdf5Ref: str):
    datasets = []
    with h5py.File(hdf5Ref, 'r') as f:
        def print_datasets(name, obj):
            if isinstance(obj, h5py.Dataset):
                datasets.append(name)
        f.visititems(print_datasets)
    return datasets

@app.get("/list_hdf5_files")
async def list_hdf5_files():
    files = [f for f in os.listdir(hdf5Folder) if f.endswith('.hdf5')]
    return {"hdf5_files": files}

@app.get("/datasets")
async def get_datasets(filename: str):
    hdf5Ref = os.path.join(hdf5Folder, filename)
    try:
        datasets = list_datasets(hdf5Ref)
        return {"available_datasets": datasets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving datasets: {e}")

@app.post("/convert_to_jpg")
async def convert_to_jpg(request: DatasetRequest):
    if not request.datasetNames:
        raise HTTPException(status_code=422, detail="datasetNames must not be empty.")
    hdf5Ref = os.path.join(hdf5Folder, request.filename)
    try:
        for dataset_name in request.datasetNames:
            convertHDF5ToJpg(hdf5Ref, dataset_name)
        return {"status": "success", "message": "All datasets converted to JPG"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting datasets: {e}")

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
