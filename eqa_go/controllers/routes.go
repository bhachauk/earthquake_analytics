package controllers

import (
	"github.com/gin-gonic/gin"
)

func RegisterMetricRoutes(router *gin.Engine) {
	homeRoute := router.Group("/")
	homeRoute.GET("/", func(c *gin.Context) {
		c.JSON(200, gin.H{"Application": "Earthquake Analytics"})
	})

	metricRoutes := router.Group("/metrics")
	{
		metricRoutes.GET("/", GetAllMetrics)
		metricRoutes.GET("/:metric", GetMetric)
	}
}
