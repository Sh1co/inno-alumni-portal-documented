import * as FileSaver from 'file-saver';
import XLSX from 'sheetjs-style';

const fileType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8';
const fileExtension = '.xlsx';

export const exportToExcel = async ({ data, fileName }) => {
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = { Sheets: { [fileName]: ws }, SheetNames: [fileName] }
    const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
    const blob_data = new Blob([excelBuffer], { type: fileType })
    FileSaver.saveAs(blob_data, fileName + fileExtension)
}


export const importFromExcel = async ({ fileName }) => {
    const ws = XLSX.utils.sheet_to_json(fileName);
    const wb = { Sheets: { 'data': ws }, SheetNames: ["data"] }
    const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
    const blob_data = new Blob([excelBuffer], { type: fileType })
    FileSaver.saveAs(blob_data, fileName + fileExtension)
}