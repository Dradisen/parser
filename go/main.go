package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"

	_ "github.com/mattn/go-sqlite3"
)

// f"https://basket-{shard_id}.wbbasket.ru/vol{vol}/part{part}/{articul}"
// url = f"{base_url}/images/c246x328/{index}.webp"
// LIST_PARSE_URL = 'https://search.wb.ru/exactmatch/ru/common/v4/search'

func initializeDb() {
	db, err := sql.Open("sqlite3", "wb.sqlite")

	if err != nil {
		fmt.Printf("Ошибка при открытии базы данных: %v\n", err)
		return
	}
	fmt.Println("База данных успешно открыта.")
	fmt.Println(db)
}

func wbLoadListAPI(dest string, query string, page int) (*http.Response, error) {
	// Запрос к API для получения списка товаров
	var (
		base_url string = "https://search.wb.ru/exactmatch/ru/common/v4/search"
		params   string = fmt.Sprintf(`?appType=1&curr=rub&dest=%s&lang=ru&query=%s&resultset=catalog&sort=popular&spp=30&page=%d`, dest, query, page)
	)

	response, err := http.Get(base_url + params)
	if err != nil {
		return nil, err
	}

	if response.StatusCode != http.StatusOK {
		fmt.Printf("|- List [%s] Ошибка запроса [%d]. Retry...\n", base_url, response.StatusCode)
		return nil, fmt.Errorf("HTTP [%d]", response.StatusCode)
	}
	fmt.Printf("|- List [%s] on Page=[%d] Ok...\n", base_url, page)
	return response, nil

}

func main() {

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Printf("Received request: %s %s\n", r.Method, r.URL.Path)
		fmt.Fprint(w, "root path server")

		response, err := wbLoadListAPI("-1257786", "query", 1)
		if err != nil {
			fmt.Printf("Ошибка: %v\n", err)
			return
		}
		var data map[string]interface{}
		if err := json.NewDecoder(response.Body).Decode(&data); err != nil {
			fmt.Printf("Ошибка при декодировании JSON: %v\n", err)
			return
		}
		defer response.Body.Close()
		fmt.Fprint(w, data)
	})
	http.ListenAndServe(":8000", nil)
}
