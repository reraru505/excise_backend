extern crate captcha;

use actix_web::{get, post, web, App, Error, HttpResponse, HttpServer, Responder};
use actix_cors::Cors;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::sync::Mutex;
use captcha::{gen, Difficulty};
use std::fs::File;
use std::io::Read;
use base64::{Engine as _, engine::general_purpose}; // Correct import
use std::path::Path;

#[derive(Deserialize, Serialize, Debug)]
struct Captcha_Data {
    image_data: String, // Base64 encoded image data
    // text: String,        // No need to send text to frontend
}

#[derive(Deserialize, Serialize, Debug)]
pub struct FormData {
    pub username: String,
    pub password: String,
    pub captcha: String, // Captcha entered by user
}

async fn submit_form(
    form: web::Json<FormData>,
    data: web::Data<AppState>,
) -> Result<HttpResponse, Error> {
    println!("submit_form called! Data: {:?}", form);

    let last_captcha = data.last_captcha.lock().unwrap();

    if form.captcha != *last_captcha {
        return Ok(HttpResponse::BadRequest().json(json!({"message": "Invalid Captcha"})));
    }

    if form.username == "testuser" && form.password == "password" {
        Ok(HttpResponse::Ok().json(json!({"message": "Loginsuccess"})))
    } else {
        Ok(HttpResponse::Unauthorized().json(json!({"message": "Invalid credentials"})))
    }
}

async fn send_captcha(data: web::Data<AppState>) -> Result<HttpResponse, Error> {
    println!("Captcha Asked");

    let captcha = gen(Difficulty::Easy);
    let captcha_chars = captcha.chars_as_string();
    println!("Captcha Generated");
    let mut last_captcha = data.last_captcha.lock().unwrap();
    *last_captcha = captcha_chars.clone();

    let png_data = captcha.as_png().unwrap(); // Get PNG data (Vec<u8>)

    println!("Captcha image loaded");

    let base64_image = general_purpose::STANDARD.encode(&png_data); // Base64 encode PNG data

    let captcha_data = Captcha_Data {
        image_data: format!("data:image/png;base64,{}", base64_image), // Correct MIME type!
    };

    println!("Captcha Sent");
    Ok(HttpResponse::Ok().json(captcha_data))
}

#[get("/api/test")]
async fn test_api() -> impl Responder {
    HttpResponse::Ok().json(json!({"message": "Test API works!"}))
}

struct AppState {
    last_captcha: Mutex<String>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let app_state = web::Data::new(AppState {
        last_captcha: Mutex::new(String::new()),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(app_state.clone())
            .wrap(
                Cors::default()
                    .allowed_origin("http://localhost:4200")
                    .allowed_methods(vec!["POST", "GET"])
                    .allowed_headers(vec!["Content-Type"]),
            )
            .service(test_api)
            .service(
                web::resource("/api/loginForm")
                    .route(web::post().to(submit_form)),
            )
            .service(
                web::resource("/api/getcaptcha")
                    .route(web::get().to(send_captcha)),
            )
    })
    .bind(("0.0.0.0", 8080))?
    .run()
    .await
}
