# starrydata_datasets

## Dataset Repository

| Repository | Availability | Update Schedule | Period |
|------------|--------------|-----------------|--------|
| [Github](https://github.com/starrydata/starrydata_datasets) | Past datasets available for download | - | until 2022/12/22 |
| [Figshare](https://figshare.com/projects/Starrydata_datasets/155129) | Past datasets available for download | Daily until 2024/06/06, then monthly | from 2022/12/22 |
| [Google Drive](https://drive.google.com/drive/folders/1OVMP7j61CJFwLtJ-qZFef9ko40Othayh) | Only the latest dataset available | Twice daily at 00:00 and 12:00 | from 2024/06/13 |


## Changelog

### 2024/06/13
- The latest datasets are now uploaded to Google Drive.

### 2024/06/06
- Fixed the character corruption issue when users open all_samples.csv in certain applications, such as Excel, by adding a BOM.
- The upload schedule to Figshare has been changed from daily to monthly.


### 2024/05/22
- Fixed the incorrect timestamp format in the dataset. For example, corrected "2024-05-17 00:00:01 JST+0900" to "2024-05-17 00:00:01 GMT+0900 (JST)".


### 2024/05/21
- The values in the XY value list were originally strings enclosed in double quotations. These double quotations were removed for easier analysis.
- e.g. ["299.8597", "324.8683"] -> [299.8597, 324.8683]

### 2024/05/16
- Added `updated_at`, `created_at`, and `composition_details` to `all_samples.csv`.

### 2022/12/22
- The dataset location was changed from this GitHub repository to [Figshare](https://figshare.com/projects/Starrydata_datasets/155129).

