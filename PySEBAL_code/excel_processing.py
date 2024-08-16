
from config import LANDSAT_INDIR, METEO_INDIR, DOCS_INDIR, SEBAL_OUTDIR
from utils import get_folders_in_folder, write_to_excel


if __name__ == "__main__":
    excel_file_path = DOCS_INDIR + 'helper.xlsx'
    folder_paths, folder_names = get_folders_in_folder(LANDSAT_INDIR)
    write_to_excel(folder_paths, folder_names, SEBAL_OUTDIR, METEO_INDIR, excel_file_path)
