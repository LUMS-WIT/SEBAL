
from config import LANDSAT_INDIR, METEO_INDIR, DOCS_INDIR, SEBAL_OUTDIR
from config import MODIS_INDIR, IMAGE_TYPE
from utils import get_folders_in_folder, write_to_excel, write_to_excel_modis


if __name__ == "__main__":

    if IMAGE_TYPE ==3:
        excel_file_path = DOCS_INDIR + 'helper_modis.xlsx'
        dates = write_to_excel_modis(MODIS_INDIR, SEBAL_OUTDIR, METEO_INDIR, excel_file_path)
        print("Dates processed:", dates)
    else:
        excel_file_path = DOCS_INDIR + 'helper_landsat.xlsx'
        folder_paths, folder_names = get_folders_in_folder(LANDSAT_INDIR)
        write_to_excel(folder_paths, folder_names, SEBAL_OUTDIR, METEO_INDIR, excel_file_path)
