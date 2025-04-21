import os
from aiohttp import web

# Set the base directory to root "/"
BASE_DIR = '/'  # The base path should be the root of the file system

async def handle(request):
    # Get the file or directory name from the URL path
    file_name = request.match_info.get('file', '')

    # Construct the full absolute path to the file or directory
    file_path = os.path.join(BASE_DIR, file_name)

    # If it's a directory
    if os.path.isdir(file_path):
        # List files in the directory
        files = os.listdir(file_path)
        file_list_html = "<ul>"

        for f in files:
            # If the item is a directory, append a trailing slash to indicate it's a directory
            item_path = os.path.join(file_name, f)  # Relative path for the link
            file_list_html += f'<li><a href="/{item_path}">{f}/</a></li>' if os.path.isdir(os.path.join(file_path, f)) else f'<li><a href="/{item_path}">{f}</a></li>'

        file_list_html += "</ul>"
        return web.Response(text=file_list_html, content_type='text/html')

    # If it's a file, return it
    elif os.path.isfile(file_path):
        return web.FileResponse(file_path)

    # If neither file nor directory exists
    else:
        return web.Response(text="File or directory not found", status=404)

# Create the web application and add the route to handle requests
app = web.Application()
app.router.add_get('/{file:.*}', handle)  # The regex ensures we can handle file or directories

# Run the app on port 5006
web.run_app(app, port=5006)
