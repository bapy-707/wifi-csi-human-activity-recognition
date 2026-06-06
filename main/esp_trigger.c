#include <stdio.h>
#include <string.h>
#include <math.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"

#include "esp_wifi.h"
#include "esp_event.h"
#include "nvs_flash.h"
#include "esp_log.h"
#include "esp_netif.h"

// ================= USER CONFIG =================
#define WIFI_SSID "TEST123"
#define WIFI_PASS "12345678"

// 🔥 CHANGE THIS:
// ESP1 → 1
// ESP2 → 2
#define DEVICE_ID 1

static const char *TAG = "CSI_SYSTEM";

static EventGroupHandle_t wifi_event_group;
#define WIFI_CONNECTED_BIT BIT0

// ================= CSI CALLBACK =================
void wifi_csi_rx_cb(void *ctx, wifi_csi_info_t *info)
{
    // Print clean data for Python
    printf("CSI_%d,", DEVICE_ID);

    for (int i = 0; i < info->len; i++) {
        printf("%d,", info->buf[i]);
    }

    printf("\n");
}

// ================= WIFI EVENTS =================
static void event_handler(void* arg,
                         esp_event_base_t event_base,
                         int32_t event_id,
                         void* event_data)
{
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    }

    else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {

        wifi_event_sta_disconnected_t* event =
            (wifi_event_sta_disconnected_t*) event_data;

        ESP_LOGI(TAG, "WiFi disconnected, reason: %d", event->reason);

        vTaskDelay(2000 / portTICK_PERIOD_MS);
        esp_wifi_connect();
    }

    else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {

        ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;

        ESP_LOGI(TAG, "Connected! IP: " IPSTR, IP2STR(&event->ip_info.ip));

        xEventGroupSetBits(wifi_event_group, WIFI_CONNECTED_BIT);
    }
}

// ================= WIFI INIT =================
void wifi_init()
{
    wifi_event_group = xEventGroupCreate();

    nvs_flash_init();
    esp_netif_init();
    esp_event_loop_create_default();
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&cfg);

    esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &event_handler, NULL);
    esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &event_handler, NULL);

    wifi_config_t wifi_config = {0};

    strcpy((char *)wifi_config.sta.ssid, WIFI_SSID);
    strcpy((char *)wifi_config.sta.password, WIFI_PASS);

    // 🔥 Stability settings
    wifi_config.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;

    wifi_config.sta.pmf_cfg.capable = true;
    wifi_config.sta.pmf_cfg.required = false;

    esp_wifi_set_mode(WIFI_MODE_STA);
    esp_wifi_set_config(WIFI_IF_STA, &wifi_config);
    esp_wifi_start();

    esp_wifi_set_ps(WIFI_PS_NONE); // disable power saving
}

// ================= CSI INIT =================
void csi_init()
{
    wifi_csi_config_t csi_config = {
        .lltf_en = true,
        .htltf_en = true,
        .stbc_htltf2_en = true,
        .ltf_merge_en = true,
        .channel_filter_en = true,
        .manu_scale = false,
        .shift = 0
    };

    esp_wifi_set_csi_config(&csi_config);
    esp_wifi_set_csi_rx_cb(wifi_csi_rx_cb, NULL);
    esp_wifi_set_csi(true);

    // 🔥 Required for CSI
    esp_wifi_set_promiscuous(true);

    ESP_LOGI(TAG, "CSI Started Successfully");
}

// ================= MAIN =================
void app_main(void)
{
    wifi_init();

    // Wait until WiFi connected
    xEventGroupWaitBits(wifi_event_group,
                        WIFI_CONNECTED_BIT,
                        pdFALSE,
                        pdTRUE,
                        portMAX_DELAY);

    ESP_LOGI(TAG, "WiFi ready, starting CSI...");

    csi_init();

    while (1) {
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
}