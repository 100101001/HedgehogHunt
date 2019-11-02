const baseUrl = "http://localhost:8080"
export const HedgeHogClient = {
    GetFindListRequest: (pageIndex, pageCount, appendDataToList) => {
        return {
            method: 'GET',
            url: baseUrl + '/found/' + pageIndex,
            data: {
                pageCount: pageCount
            },
            success: appendDataToList
        }
    }
}