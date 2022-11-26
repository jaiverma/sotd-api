open Lwt
open Cohttp
open Cohttp_lwt_unix
module Y = Yojson.Safe

type spotify_config =
  { client_id : string
  ; client_secret : string
  ; bearer_token : string option
  }

let auth_and_get_token conf =
  let url = Uri.of_string "https://accounts.spotify.com/api/token" in
  let token = Base64.encode_exn @@ conf.client_id ^ ":" ^ conf.client_secret in
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
  >|= fun body ->
  let token = Y.from_string body |> Y.Util.member "access_token" |> Y.Util.to_string in
  { client_id = conf.client_id
  ; client_secret = conf.client_secret
  ; bearer_token = Some token
  }
;;

let api_request ?endpoint ?params url config =
  (* validate config *)
  match config.bearer_token with
  | None -> Lwt.return @@ Error "bearer token not set"
  | Some token ->
    let url =
      match endpoint with
      | Some endpoint -> url ^ endpoint
      | None -> url
    in
    let url =
      match params with
      | Some params -> Uri.add_query_params (Uri.of_string url) params
      | None -> Uri.of_string url
    in
    let headers = Header.of_list [ "Authorization", "Bearer " ^ token ] in
    Client.get ~headers url
    >>= fun (resp, body) ->
    Printf.printf "Response code: %d\n" (resp |> Response.status |> Code.code_of_status);
    Cohttp_lwt.Body.to_string body >|= fun body -> Ok body
;;

let setup_config () =
  { client_id = Sys.getenv "CLIENT_ID"
  ; client_secret = Sys.getenv "CLIENT_SECRET"
  ; bearer_token = None
  }
;;

let main =
  auth_and_get_token @@ setup_config ()
  >>= fun config ->
  let url = "https://api.spotify.com/v1" in
  let params =
    ( "fields"
    , [ "tracks.next,tracks.items(added_at,track.name,track.uri,track.external_urls.spotify,track(album(name,artists,images,release_date)))"
      ] )
  in
  api_request url config ~endpoint:"/playlists/0IKkPLCIcb0NlBiZ0wjSkG" ~params:[ params ]
  >|= function
  | Ok resp -> Printf.printf "%s\n" resp
  | Error e -> Printf.printf "%s\n" e
;;

let () = Lwt_main.run main
