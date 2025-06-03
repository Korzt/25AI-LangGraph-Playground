package models

type Product struct {
    ID        int      `json:"id"`
    Name      string   `json:"name"`
    Category  string   `json:"category"`
    Price     float64  `json:"price"`
    InStock   bool     `json:"in_stock"`
    Rating    float64  `json:"rating"`
    Tags      []string `json:"tags"`
    CreatedAt string   `json:"created_at"`
}