require "socket"
require "json"

# Ruby ↔ Python 桥接
module Command
  def self.api(command)
    begin
      socket = TCPSocket.new("127.0.0.1", 50505)
      socket.puts({ command: command }.to_json)
      res = JSON.parse(socket.gets(nil))
      socket.close
      puts "[Python Response] #{res["result"] || res["error"]}"
    rescue => e
      puts "Unable to connect to Python Bridge:#{e}"
    end
  end

  def self.run(cmd)
    puts "▶ Run system commands:#{cmd}"
    system("python command Line.py #{cmd}")
  end
end

class XClass
  def self.inherited(subclass)
    puts "Loading X++ classes: #{subclass}"
  end
end
