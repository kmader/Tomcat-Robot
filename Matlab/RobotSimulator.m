% RobotSimulator
% Simulate the robot for testing out epics and python code
%
% Usage - RobotSimulator(message, output_port, number_of_retries)
%function RobotSimulator(message, output_port, number_of_retries)
number_of_retries=3;
output_port=50001;
message='start';

import java.net.ServerSocket
import java.io.*

retry             = 0;

server_socket  = [];
output_socket  = [];

while true

    retry = retry + 1;

    try
        if ((number_of_retries > 0) && (retry > number_of_retries))
            fprintf(1, 'Too many retries\n');
            break;
        end

        fprintf(1, ['Try %d waiting for client to connect to this ' ...
            'host on port : %d\n'], retry, output_port);

        [jnk,hostname]=system('echo $HOSTNAME');

        disp(['Current IP is:' hostname])
        % wait for 60 seconds for client to connect server socket
        server_socket = ServerSocket(output_port);
        server_socket.setSoTimeout(60000);

        output_socket = server_socket.accept;

        fprintf(1, 'Client connected\n');
                    output_stream   = output_socket.getOutputStream;
            d_output_stream = DataOutputStream(output_stream);
        while 1


            % output the data over the DataOutputStream
            % Convert to stream of bytes
            fprintf(1, 'Writing %d bytes\n', length(message))
            d_output_stream.writeBytes(char(message));
            d_output_stream.flush;
            bytes_available = output_stream.available;
            fprintf(1, 'Reading %d bytes\n', bytes_available);

            message = zeros(1, bytes_available, 'uint8');
            for i = 1:bytes_available
                message(i) = d_output_stream.readByte;
            end

            message = char(message);
            % clean up
        end
        server_socket.close;
        output_socket.close;
        break;

    catch
        if ~isempty(server_socket)
            server_socket.close
        end

        if ~isempty(output_socket)
            output_socket.close
        end

        % pause before retrying
        pause(1);
    end
end

