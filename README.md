# Energy Independence

This tool scans a specified geographical area from a GeoJSON file to measure energy independence, outputs the results as GeoJSON files with polygon shapes for each detected solar panel.

## Dependencies

Make sure you have the following libraries and tools installed (some may be pre-installed):

- Python 3.x
- [NumPy](https://numpy.org/)
- [Requests](https://docs.python-requests.org/en/latest/)
- [Pillow](https://pillow.readthedocs.io/en/stable/) (PIL fork)
- [Matplotlib](https://matplotlib.org/)
- [GitPython](https://gitpython.readthedocs.io/en/stable/)
- [GeoJSON](https://pypi.org/project/geojson/)
- [subprocess](https://docs.python.org/3/library/subprocess.html)
- [math](https://docs.python.org/3/library/math.html)

You can install the required dependencies using the following command:
```bash
pip install numpy requests Pillow matplotlib gitpython
```

## How to Use

1. **Prepare your input:**

   - Place the path to the input **GeoJSON file** containing the input geographical coordinates into line 32.
    ```python
   file_path = #insert GeoJSON file path here
    ```

2. **Configure paths:**

   - **Line 14**: Modify the path to match the directory you would like to run the code in
   - Download and add the `best.pt` model file to the **same path**
     ```python
     output_file_path = #insert path here
     ```


3. **Run the code**
   - Outputs will be in **/outputs** in your desired path from step 2. 
   - Each GeoJSON file corresponds to each input geographical coordinate, where  each GeoJSON file has the polygon shapes of each solar panel.
