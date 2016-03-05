using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Net.Sockets;
using System.Net;
using System.Threading;

namespace WindowsFormsApplication7
{
    public partial class Form1 : Form
    {
        Socket client;

        public Form1()
        {
            InitializeComponent();
            ThreadStart tstart=new ThreadStart(Thread_Function);
            Thread tserver = new Thread(tstart);
            tserver.IsBackground = true;
            tserver.Start();
        }
        private void Thread_Function()
        {

            Socket s = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            IPAddress IP = IPAddress.Parse("127.0.0.1");
            IPEndPoint address = new IPEndPoint(IP, 1234);
            s.Bind(address);
            s.Listen(1);
            client = s.Accept();

            while (true)
                ClientList();
        }
        private void ClientList()
        {
            string Recieved_Massage = Recieve_Function();
            if (Recieved_Massage.Contains("disconnected"))
            {
                string[] arr=Recieved_Massage.Split('$');
                string[] arr2 = arr[1].Split('#');
                string IP = arr2[0];
                string Port = arr2[1];
                foreach (ListViewItem item in listView1.Items)
                {
                    if (item.SubItems[1].Text == IP && item.SubItems[2].Text == Port)
                        listView1.Items.Remove(item);
                }
            }
            else
            {
                string[] arr = Recieved_Massage.Split('#');
                string IP = arr[0];
                string Port = arr[1];
                ListViewItem item = new ListViewItem("1");
                item.SubItems.Add(IP);
                item.SubItems.Add(Port);
                listView1.Items.Add(item);
            }
            
        }
        private string Recieve_Function()
        {
            byte[] byteBuffer = new byte[1024];
            int iLength = client.Receive(byteBuffer);
            return Encoding.UTF8.GetString(byteBuffer).Substring(0, iLength);

        }
        private void Send_Function(string message)
        {
            byte[] byteBuffer = Encoding.UTF8.GetBytes(message);
            int iLength = client.Send(byteBuffer);
            
        }

        private bool Check_Selected_Line()
        {
            if (listView1.SelectedItems.Count > 0)
                return true;
            else return false;
            
        }
        private void Check_Exceptions()
        {
            string process_name="";
            string a = "";

            while (!Check_Selected_Line())
            { }
            string IP=listView1.SelectedItems[0].SubItems[1].Text;
            string port = listView1.SelectedItems[0].SubItems[2].Text;

            Dictionary<string, bool> exceptions = new Dictionary<string, bool>()
            {
                {"wmp",false},{"youtube",false},{"cpu",false},{"process",false}
            };

            if (checkBox1.Checked == true)
                exceptions["wmp"] = true;
            if (checkBox2.Checked == true)
                exceptions["youtube"] = true;
            if (checkBox3.Checked == true)
                exceptions["cpu"] = true;
            if (checkBox4.Checked == true)
            {
                exceptions["process"] = true;
                process_name = textBox1.Text;
            }
            foreach (KeyValuePair<string, bool> kvp in exceptions)
            {
                a += kvp.Value.ToString()+"#";
                if (kvp.Key == "process"&&kvp.Value==true)
                    a += process_name;
            }
            string message = IP + "$" + port+"$"+a+"$"+textBox2.Text;
            Send_Function(message);

            string Recieved_Massage = Recieve_Function();
            richTextBox1.Text += Recieved_Massage;

        }

        private RichTextBox str(bool p)
        {
            throw new NotImplementedException();
        }
        private void listView1_SelectedIndexChanged(object sender, EventArgs e)
        {
            
        }

        private void Form1_Load(object sender, EventArgs e)
        {

        }

        private void groupBox1_Enter(object sender, EventArgs e)
        {

        }

        private void groupBox2_Enter(object sender, EventArgs e)
        {

        }

        private void label2_Click(object sender, EventArgs e)
        {

        }

        private void progressBar1_Click(object sender, EventArgs e)
        {
            
        }

        private void button1_Click(object sender, EventArgs e)
        {
            int time = Int32.Parse(textBox2.Text);
            time = time * 600;
            timer1.Interval=time;
            this.timer1.Start();
            Check_Exceptions();
        }

        private void checkBox1_CheckedChanged(object sender, EventArgs e)
        {

        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            this.progressBar1.Increment(1);
        }

        private void textBox2_TextChanged(object sender, EventArgs e)
        {

        }

        private void groupBox3_Enter(object sender, EventArgs e)
        {

        }
    }
}
