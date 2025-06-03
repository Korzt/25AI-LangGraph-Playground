package main

import (
	"encoding/json"
	"net/http"

	"go-json-server/models"
	"go-json-server/utils"
)

var products []models.Product

func main() {
	products = utils.LoadProducts("data/products.json")

	http.HandleFunc("/api/products", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(products)
	})

	println("🚀 Server running at http://localhost:3000")
	http.ListenAndServe(":3000", nil)
}
