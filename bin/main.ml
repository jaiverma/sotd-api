open Lwt
open Cohttp
open Cohttp_lwt_unix

let auth_and_get_token () =
  let url = Uri.of_string "https://accounts.spotify.com/api/token" in
  let client_id = Sys.getenv "CLIENT_ID" in
  let client_secret = Sys.getenv "CLIENT_SECRET" in
  let token = Base64.encode_exn @@ client_id ^ ":" ^ client_secret in
  let headers =
    Header.of_list
      [ "Authorization", "Basic " ^ token
      ; "Content-Type", "application/x-www-form-urlencoded"
      ]
  in
  let body =
    Cohttp_lwt.Body.of_string
    @@ Uri.encoded_of_query [ "grant_type", [ "client_credentials" ] ]
  in
  Client.post ~body ~headers url
  >>= fun (resp, body) ->
  Printf.printf "Response code: %d\n" (resp |> Response.status |> Code.code_of_status);
  Cohttp_lwt.Body.to_string body
;;

let () =
  let body = Lwt_main.run @@ auth_and_get_token () in
  print_endline @@ body ^ "\n"
;;
