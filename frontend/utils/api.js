const baseUrl = "http://localhost:8080"
export const HedgeHogClient = {
    GetFindListRequest: (id) => {
        return {
            method: 'GET',
            url: baseUrl + '/found/' + id
        }
    }
}