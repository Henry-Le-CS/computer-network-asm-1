<h2>Computer network</h2>
<h3>Assignment 1: Develop  a network application</h3>

<h4>A. How to run locally (1 machine)</h4>

<ul>
    <li>
        Copy the folder Client as much as you want
    </li>
    <li>
        Paste IP, port of your machine in server_host, server_port of server.py and all client.py
    </li>
    <li>
        Open terminal for server and clients
    </li>
    <li>
        For 1 terminal, run: cd server && python3 server.py
    </li>
    <li>
        For the other, run: cd your_client_dir_name && python3 client.py --hostname=your_client_name. For now, the client should be designed uniquely by the users.
    </li>
    <li>
        Create the files inside the client folder. Then publish it with: publish file_location file_name
    </li>
    <li>
        On other client, you can run: fetch file_name, select the node and download the file.
    </li>
    <li>
        Use the server command line to ping the client with: ping client_name
    </li>
    <li>
        Use the server command line to discover the client's current published files with: discover client_name
    </li>
</ul>
